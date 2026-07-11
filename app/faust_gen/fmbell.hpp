/* ------------------------------------------------------------
name: "fmbell"
Code generated with Faust 2.70.3 (https://faust.grame.fr)
Compilation options: -lang cpp -ct 1 -cn Fmbell -es 1 -mcd 16 -mdd 1024 -mdy 33 -single -ftz 0
------------------------------------------------------------ */

#ifndef  __Fmbell_H__
#define  __Fmbell_H__

#ifndef FAUSTFLOAT
#define FAUSTFLOAT float
#endif 

#include <algorithm>
#include <cmath>
#include <cstdint>
#include <math.h>

#ifndef FAUSTCLASS 
#define FAUSTCLASS Fmbell
#endif

#ifdef __APPLE__ 
#define exp10f __exp10f
#define exp10 __exp10
#endif

#if defined(_WIN32)
#define RESTRICT __restrict
#else
#define RESTRICT __restrict__
#endif

class FmbellSIG0 {
	
  private:
	
	int iVec2[2];
	int iRec1[2];
	
  public:
	
	int getNumInputsFmbellSIG0() {
		return 0;
	}
	int getNumOutputsFmbellSIG0() {
		return 1;
	}
	
	void instanceInitFmbellSIG0(int sample_rate) {
		for (int l3 = 0; l3 < 2; l3 = l3 + 1) {
			iVec2[l3] = 0;
		}
		for (int l4 = 0; l4 < 2; l4 = l4 + 1) {
			iRec1[l4] = 0;
		}
	}
	
	void fillFmbellSIG0(int count, float* table) {
		for (int i1 = 0; i1 < count; i1 = i1 + 1) {
			iVec2[0] = 1;
			iRec1[0] = (iVec2[1] + iRec1[1]) % 65536;
			table[i1] = std::sin(9.58738e-05f * float(iRec1[0]));
			iVec2[1] = iVec2[0];
			iRec1[1] = iRec1[0];
		}
	}

};

static FmbellSIG0* newFmbellSIG0() { return (FmbellSIG0*)new FmbellSIG0(); }
static void deleteFmbellSIG0(FmbellSIG0* dsp) { delete dsp; }

static float ftbl0FmbellSIG0[65536];

class Fmbell : public dsp {
	
 private:
	
	int iVec0[2];
	FAUSTFLOAT fButton0;
	float fVec1[2];
	int iRec0[2];
	int fSampleRate;
	float fConst0;
	float fConst1;
	float fConst2;
	FAUSTFLOAT fHslider0;
	FAUSTFLOAT fHslider1;
	FAUSTFLOAT fHslider2;
	FAUSTFLOAT fHslider3;
	float fConst3;
	float fRec3[2];
	float fRec2[2];
	FAUSTFLOAT fHslider4;
	
 public:
	Fmbell() {}

	void metadata(Meta* m) { 
		m->declare("basics.lib/name", "Faust Basic Element Library");
		m->declare("basics.lib/tabulateNd", "Copyright (C) 2023 Bart Brouns <bart@magnetophon.nl>");
		m->declare("basics.lib/version", "1.12.0");
		m->declare("compile_options", "-lang cpp -ct 1 -cn Fmbell -es 1 -mcd 16 -mdd 1024 -mdy 33 -single -ftz 0");
		m->declare("envelopes.lib/ar:author", "Yann Orlarey, Stéphane Letz");
		m->declare("envelopes.lib/author", "GRAME");
		m->declare("envelopes.lib/copyright", "GRAME");
		m->declare("envelopes.lib/license", "LGPL with exception");
		m->declare("envelopes.lib/name", "Faust Envelope Library");
		m->declare("envelopes.lib/version", "1.3.0");
		m->declare("filename", "fmbell.dsp");
		m->declare("maths.lib/author", "GRAME");
		m->declare("maths.lib/copyright", "GRAME");
		m->declare("maths.lib/license", "LGPL with exception");
		m->declare("maths.lib/name", "Faust Math Library");
		m->declare("maths.lib/version", "2.7.0");
		m->declare("name", "fmbell");
		m->declare("oscillators.lib/name", "Faust Oscillator Library");
		m->declare("oscillators.lib/version", "1.5.0");
		m->declare("platform.lib/name", "Generic Platform Library");
		m->declare("platform.lib/version", "1.3.0");
	}

	virtual int getNumInputs() {
		return 0;
	}
	virtual int getNumOutputs() {
		return 2;
	}
	
	static void classInit(int sample_rate) {
		FmbellSIG0* sig0 = newFmbellSIG0();
		sig0->instanceInitFmbellSIG0(sample_rate);
		sig0->fillFmbellSIG0(65536, ftbl0FmbellSIG0);
		deleteFmbellSIG0(sig0);
	}
	
	virtual void instanceConstants(int sample_rate) {
		fSampleRate = sample_rate;
		fConst0 = std::min<float>(1.92e+05f, std::max<float>(1.0f, float(fSampleRate)));
		fConst1 = std::max<float>(1.0f, 0.002f * fConst0);
		fConst2 = 1.0f / fConst1;
		fConst3 = 1.0f / fConst0;
	}
	
	virtual void instanceResetUserInterface() {
		fButton0 = FAUSTFLOAT(0.0f);
		fHslider0 = FAUSTFLOAT(2.5f);
		fHslider1 = FAUSTFLOAT(1.2f);
		fHslider2 = FAUSTFLOAT(4.4e+02f);
		fHslider3 = FAUSTFLOAT(3.5f);
		fHslider4 = FAUSTFLOAT(0.5f);
	}
	
	virtual void instanceClear() {
		for (int l0 = 0; l0 < 2; l0 = l0 + 1) {
			iVec0[l0] = 0;
		}
		for (int l1 = 0; l1 < 2; l1 = l1 + 1) {
			fVec1[l1] = 0.0f;
		}
		for (int l2 = 0; l2 < 2; l2 = l2 + 1) {
			iRec0[l2] = 0;
		}
		for (int l5 = 0; l5 < 2; l5 = l5 + 1) {
			fRec3[l5] = 0.0f;
		}
		for (int l6 = 0; l6 < 2; l6 = l6 + 1) {
			fRec2[l6] = 0.0f;
		}
	}
	
	virtual void init(int sample_rate) {
		classInit(sample_rate);
		instanceInit(sample_rate);
	}
	
	virtual void instanceInit(int sample_rate) {
		instanceConstants(sample_rate);
		instanceResetUserInterface();
		instanceClear();
	}
	
	virtual Fmbell* clone() {
		return new Fmbell();
	}
	
	virtual int getSampleRate() {
		return fSampleRate;
	}
	
	virtual void buildUserInterface(UI* ui_interface) {
		ui_interface->openVerticalBox("fmbell");
		ui_interface->addHorizontalSlider("bright", &fHslider1, FAUSTFLOAT(1.2f), FAUSTFLOAT(0.1f), FAUSTFLOAT(3.0f), FAUSTFLOAT(0.01f));
		ui_interface->addHorizontalSlider("decay", &fHslider0, FAUSTFLOAT(2.5f), FAUSTFLOAT(0.3f), FAUSTFLOAT(6.0f), FAUSTFLOAT(0.01f));
		ui_interface->addHorizontalSlider("freq", &fHslider2, FAUSTFLOAT(4.4e+02f), FAUSTFLOAT(2e+01f), FAUSTFLOAT(6e+03f), FAUSTFLOAT(0.001f));
		ui_interface->addHorizontalSlider("gain", &fHslider4, FAUSTFLOAT(0.5f), FAUSTFLOAT(0.0f), FAUSTFLOAT(1.0f), FAUSTFLOAT(0.01f));
		ui_interface->addButton("gate", &fButton0);
		ui_interface->addHorizontalSlider("ratio", &fHslider3, FAUSTFLOAT(3.5f), FAUSTFLOAT(0.5f), FAUSTFLOAT(8.0f), FAUSTFLOAT(0.01f));
		ui_interface->closeBox();
	}
	
	virtual void compute(int count, FAUSTFLOAT** RESTRICT inputs, FAUSTFLOAT** RESTRICT outputs) {
		FAUSTFLOAT* output0 = outputs[0];
		FAUSTFLOAT* output1 = outputs[1];
		float fSlow0 = float(fButton0);
		float fSlow1 = 1.0f / std::max<float>(1.0f, fConst0 * float(fHslider0));
		float fSlow2 = 1.0f / std::max<float>(1.0f, fConst0 * float(fHslider1));
		float fSlow3 = float(fHslider2);
		float fSlow4 = float(fHslider3);
		float fSlow5 = fConst3 * fSlow4 * fSlow3;
		float fSlow6 = fConst3 * fSlow3;
		float fSlow7 = float(fHslider4);
		for (int i0 = 0; i0 < count; i0 = i0 + 1) {
			iVec0[0] = 1;
			fVec1[0] = fSlow0;
			iRec0[0] = (fSlow0 > fVec1[1]) + (fSlow0 <= fVec1[1]) * (iRec0[1] + (iRec0[1] > 0));
			float fTemp0 = float(iRec0[0]);
			float fTemp1 = fConst2 * fTemp0;
			float fTemp2 = fConst1 - fTemp0;
			int iTemp3 = 1 - iVec0[1];
			float fTemp4 = ((iTemp3) ? 0.0f : fSlow5 + fRec3[1]);
			fRec3[0] = fTemp4 - std::floor(fTemp4);
			float fTemp5 = ((iTemp3) ? 0.0f : fRec2[1] + fSlow6 * (fSlow4 * ftbl0FmbellSIG0[std::max<int>(0, std::min<int>(int(65536.0f * fRec3[0]), 65535))] * std::max<float>(0.0f, std::min<float>(fTemp1, fSlow2 * fTemp2 + 1.0f)) + 1.0f));
			fRec2[0] = fTemp5 - std::floor(fTemp5);
			float fTemp6 = fSlow7 * ftbl0FmbellSIG0[std::max<int>(0, std::min<int>(int(65536.0f * fRec2[0]), 65535))] * std::max<float>(0.0f, std::min<float>(fTemp1, fSlow1 * fTemp2 + 1.0f));
			output0[i0] = FAUSTFLOAT(fTemp6);
			output1[i0] = FAUSTFLOAT(fTemp6);
			iVec0[1] = iVec0[0];
			fVec1[1] = fVec1[0];
			iRec0[1] = iRec0[0];
			fRec3[1] = fRec3[0];
			fRec2[1] = fRec2[0];
		}
	}

};

#endif

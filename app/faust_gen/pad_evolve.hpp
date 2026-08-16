/* ------------------------------------------------------------
name: "pad_evolve"
Code generated with Faust 2.70.3 (https://faust.grame.fr)
Compilation options: -lang cpp -ct 1 -cn PadEvolve -es 1 -mcd 16 -mdd 1024 -mdy 33 -single -ftz 0
------------------------------------------------------------ */

#ifndef  __PadEvolve_H__
#define  __PadEvolve_H__

#ifndef FAUSTFLOAT
#define FAUSTFLOAT float
#endif 

#include <algorithm>
#include <cmath>
#include <cstdint>
#include <math.h>

#ifndef FAUSTCLASS 
#define FAUSTCLASS PadEvolve
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

class PadEvolveSIG0 {
	
  private:
	
	int iVec0[2];
	int iRec0[2];
	
  public:
	
	int getNumInputsPadEvolveSIG0() {
		return 0;
	}
	int getNumOutputsPadEvolveSIG0() {
		return 1;
	}
	
	void instanceInitPadEvolveSIG0(int sample_rate) {
		for (int l0 = 0; l0 < 2; l0 = l0 + 1) {
			iVec0[l0] = 0;
		}
		for (int l1 = 0; l1 < 2; l1 = l1 + 1) {
			iRec0[l1] = 0;
		}
	}
	
	void fillPadEvolveSIG0(int count, float* table) {
		for (int i1 = 0; i1 < count; i1 = i1 + 1) {
			iVec0[0] = 1;
			iRec0[0] = (iVec0[1] + iRec0[1]) % 65536;
			table[i1] = std::sin(9.58738e-05f * float(iRec0[0]));
			iVec0[1] = iVec0[0];
			iRec0[1] = iRec0[0];
		}
	}

};

static PadEvolveSIG0* newPadEvolveSIG0() { return (PadEvolveSIG0*)new PadEvolveSIG0(); }
static void deletePadEvolveSIG0(PadEvolveSIG0* dsp) { delete dsp; }

static float ftbl0PadEvolveSIG0[65536];
static float PadEvolve_faustpower2_f(float value) {
	return value * value;
}

class PadEvolve : public dsp {
	
 private:
	
	int iVec1[2];
	int fSampleRate;
	float fConst0;
	float fConst1;
	float fRec1[2];
	float fConst2;
	float fRec2[2];
	FAUSTFLOAT fHslider0;
	float fConst3;
	FAUSTFLOAT fButton0;
	float fVec2[2];
	int iRec3[2];
	FAUSTFLOAT fHslider1;
	float fRec4[2];
	FAUSTFLOAT fHslider2;
	float fConst4;
	FAUSTFLOAT fHslider3;
	float fConst5;
	float fRec6[2];
	float fConst6;
	float fRec8[2];
	float fRec9[2];
	float fRec5[3];
	FAUSTFLOAT fHslider4;
	
 public:
	PadEvolve() {}

	void metadata(Meta* m) { 
		m->declare("basics.lib/name", "Faust Basic Element Library");
		m->declare("basics.lib/tabulateNd", "Copyright (C) 2023 Bart Brouns <bart@magnetophon.nl>");
		m->declare("basics.lib/version", "1.12.0");
		m->declare("compile_options", "-lang cpp -ct 1 -cn PadEvolve -es 1 -mcd 16 -mdd 1024 -mdy 33 -single -ftz 0");
		m->declare("envelopes.lib/adsr:author", "Yann Orlarey and Andrey Bundin");
		m->declare("envelopes.lib/author", "GRAME");
		m->declare("envelopes.lib/copyright", "GRAME");
		m->declare("envelopes.lib/license", "LGPL with exception");
		m->declare("envelopes.lib/name", "Faust Envelope Library");
		m->declare("envelopes.lib/version", "1.3.0");
		m->declare("filename", "pad_evolve.dsp");
		m->declare("filters.lib/fir:author", "Julius O. Smith III");
		m->declare("filters.lib/fir:copyright", "Copyright (C) 2003-2019 by Julius O. Smith III <jos@ccrma.stanford.edu>");
		m->declare("filters.lib/fir:license", "MIT-style STK-4.3 license");
		m->declare("filters.lib/iir:author", "Julius O. Smith III");
		m->declare("filters.lib/iir:copyright", "Copyright (C) 2003-2019 by Julius O. Smith III <jos@ccrma.stanford.edu>");
		m->declare("filters.lib/iir:license", "MIT-style STK-4.3 license");
		m->declare("filters.lib/lowpass0_highpass1", "MIT-style STK-4.3 license");
		m->declare("filters.lib/lowpass0_highpass1:author", "Julius O. Smith III");
		m->declare("filters.lib/lowpass:author", "Julius O. Smith III");
		m->declare("filters.lib/lowpass:copyright", "Copyright (C) 2003-2019 by Julius O. Smith III <jos@ccrma.stanford.edu>");
		m->declare("filters.lib/lowpass:license", "MIT-style STK-4.3 license");
		m->declare("filters.lib/name", "Faust Filters Library");
		m->declare("filters.lib/tf2:author", "Julius O. Smith III");
		m->declare("filters.lib/tf2:copyright", "Copyright (C) 2003-2019 by Julius O. Smith III <jos@ccrma.stanford.edu>");
		m->declare("filters.lib/tf2:license", "MIT-style STK-4.3 license");
		m->declare("filters.lib/tf2s:author", "Julius O. Smith III");
		m->declare("filters.lib/tf2s:copyright", "Copyright (C) 2003-2019 by Julius O. Smith III <jos@ccrma.stanford.edu>");
		m->declare("filters.lib/tf2s:license", "MIT-style STK-4.3 license");
		m->declare("filters.lib/version", "1.3.0");
		m->declare("maths.lib/author", "GRAME");
		m->declare("maths.lib/copyright", "GRAME");
		m->declare("maths.lib/license", "LGPL with exception");
		m->declare("maths.lib/name", "Faust Math Library");
		m->declare("maths.lib/version", "2.7.0");
		m->declare("name", "pad_evolve");
		m->declare("oscillators.lib/name", "Faust Oscillator Library");
		m->declare("oscillators.lib/saw2ptr:author", "Julius O. Smith III");
		m->declare("oscillators.lib/saw2ptr:license", "STK-4.3");
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
		PadEvolveSIG0* sig0 = newPadEvolveSIG0();
		sig0->instanceInitPadEvolveSIG0(sample_rate);
		sig0->fillPadEvolveSIG0(65536, ftbl0PadEvolveSIG0);
		deletePadEvolveSIG0(sig0);
	}
	
	virtual void instanceConstants(int sample_rate) {
		fSampleRate = sample_rate;
		fConst0 = std::min<float>(1.92e+05f, std::max<float>(1.0f, float(fSampleRate)));
		fConst1 = 0.073f / fConst0;
		fConst2 = 0.017f / fConst0;
		fConst3 = 3.1415927f / fConst0;
		fConst4 = 0.2f / std::max<float>(1.0f, 0.6f * fConst0);
		fConst5 = 1.0f / fConst0;
		fConst6 = 0.113f / fConst0;
	}
	
	virtual void instanceResetUserInterface() {
		fHslider0 = FAUSTFLOAT(0.5f);
		fButton0 = FAUSTFLOAT(0.0f);
		fHslider1 = FAUSTFLOAT(1.6f);
		fHslider2 = FAUSTFLOAT(1.2f);
		fHslider3 = FAUSTFLOAT(2.2e+02f);
		fHslider4 = FAUSTFLOAT(0.5f);
	}
	
	virtual void instanceClear() {
		for (int l2 = 0; l2 < 2; l2 = l2 + 1) {
			iVec1[l2] = 0;
		}
		for (int l3 = 0; l3 < 2; l3 = l3 + 1) {
			fRec1[l3] = 0.0f;
		}
		for (int l4 = 0; l4 < 2; l4 = l4 + 1) {
			fRec2[l4] = 0.0f;
		}
		for (int l5 = 0; l5 < 2; l5 = l5 + 1) {
			fVec2[l5] = 0.0f;
		}
		for (int l6 = 0; l6 < 2; l6 = l6 + 1) {
			iRec3[l6] = 0;
		}
		for (int l7 = 0; l7 < 2; l7 = l7 + 1) {
			fRec4[l7] = 0.0f;
		}
		for (int l8 = 0; l8 < 2; l8 = l8 + 1) {
			fRec6[l8] = 0.0f;
		}
		for (int l9 = 0; l9 < 2; l9 = l9 + 1) {
			fRec8[l9] = 0.0f;
		}
		for (int l10 = 0; l10 < 2; l10 = l10 + 1) {
			fRec9[l10] = 0.0f;
		}
		for (int l11 = 0; l11 < 3; l11 = l11 + 1) {
			fRec5[l11] = 0.0f;
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
	
	virtual PadEvolve* clone() {
		return new PadEvolve();
	}
	
	virtual int getSampleRate() {
		return fSampleRate;
	}
	
	virtual void buildUserInterface(UI* ui_interface) {
		ui_interface->openVerticalBox("pad_evolve");
		ui_interface->addHorizontalSlider("attack", &fHslider2, FAUSTFLOAT(1.2f), FAUSTFLOAT(0.05f), FAUSTFLOAT(4.0f), FAUSTFLOAT(0.01f));
		ui_interface->addHorizontalSlider("evolve_depth", &fHslider0, FAUSTFLOAT(0.5f), FAUSTFLOAT(0.0f), FAUSTFLOAT(1.0f), FAUSTFLOAT(0.01f));
		ui_interface->addHorizontalSlider("freq", &fHslider3, FAUSTFLOAT(2.2e+02f), FAUSTFLOAT(2e+01f), FAUSTFLOAT(2e+03f), FAUSTFLOAT(0.001f));
		ui_interface->addHorizontalSlider("gain", &fHslider4, FAUSTFLOAT(0.5f), FAUSTFLOAT(0.0f), FAUSTFLOAT(1.0f), FAUSTFLOAT(0.01f));
		ui_interface->addButton("gate", &fButton0);
		ui_interface->addHorizontalSlider("release", &fHslider1, FAUSTFLOAT(1.6f), FAUSTFLOAT(0.1f), FAUSTFLOAT(6.0f), FAUSTFLOAT(0.01f));
		ui_interface->closeBox();
	}
	
	virtual void compute(int count, FAUSTFLOAT** RESTRICT inputs, FAUSTFLOAT** RESTRICT outputs) {
		FAUSTFLOAT* output0 = outputs[0];
		FAUSTFLOAT* output1 = outputs[1];
		float fSlow0 = float(fHslider0);
		float fSlow1 = 0.5f * (0.65f * fSlow0 + 0.35f);
		float fSlow2 = float(fButton0);
		int iSlow3 = fSlow2 == 0.0f;
		float fSlow4 = 1.0f / std::max<float>(1.0f, fConst0 * float(fHslider1));
		float fSlow5 = std::max<float>(1.0f, fConst0 * float(fHslider2));
		float fSlow6 = 1.0f / fSlow5;
		float fSlow7 = float(fHslider3);
		float fSlow8 = std::max<float>(1.1920929e-07f, std::fabs(1.0040516f * fSlow7));
		float fSlow9 = fConst5 * fSlow8;
		float fSlow10 = 1.0f - fConst0 / fSlow8;
		float fSlow11 = std::max<float>(1.1920929e-07f, std::fabs(0.9959648f * fSlow7));
		float fSlow12 = fConst5 * fSlow11;
		float fSlow13 = 1.0f - fConst0 / fSlow11;
		float fSlow14 = 0.42f * float(fHslider4);
		for (int i0 = 0; i0 < count; i0 = i0 + 1) {
			iVec1[0] = 1;
			int iTemp0 = 1 - iVec1[1];
			float fTemp1 = ((iTemp0) ? 0.0f : fConst1 + fRec1[1]);
			fRec1[0] = fTemp1 - std::floor(fTemp1);
			float fTemp2 = ((iTemp0) ? 0.0f : fConst2 + fRec2[1]);
			fRec2[0] = fTemp2 - std::floor(fTemp2);
			float fTemp3 = std::tan(fConst3 * (fSlow1 * (1.4e+03f * ftbl0PadEvolveSIG0[std::max<int>(0, std::min<int>(int(65536.0f * fRec2[0]), 65535))] + 2.6e+03f) * (ftbl0PadEvolveSIG0[std::max<int>(0, std::min<int>(int(65536.0f * fRec1[0]), 65535))] + 1.0f) + 9e+02f));
			float fTemp4 = 1.0f / fTemp3;
			float fTemp5 = (fTemp4 + 1.4142135f) / fTemp3 + 1.0f;
			fVec2[0] = fSlow2;
			iRec3[0] = iSlow3 * (iRec3[1] + 1);
			fRec4[0] = fSlow2 + fRec4[1] * float(fVec2[1] >= fSlow2);
			float fTemp6 = fSlow9 + fRec6[1] + -1.0f;
			int iTemp7 = fTemp6 < 0.0f;
			float fTemp8 = fSlow9 + fRec6[1];
			fRec6[0] = ((iTemp7) ? fTemp8 : fTemp6);
			float fRec7 = ((iTemp7) ? fTemp8 : fSlow9 + fRec6[1] + fSlow10 * fTemp6);
			float fTemp9 = ((iTemp0) ? 0.0f : fConst6 + fRec8[1]);
			fRec8[0] = fTemp9 - std::floor(fTemp9);
			float fTemp10 = fSlow0 * ftbl0PadEvolveSIG0[std::max<int>(0, std::min<int>(int(65536.0f * fRec8[0]), 65535))] + 1.0f;
			float fTemp11 = fSlow12 + fRec9[1] + -1.0f;
			int iTemp12 = fTemp11 < 0.0f;
			float fTemp13 = fSlow12 + fRec9[1];
			fRec9[0] = ((iTemp12) ? fTemp13 : fTemp11);
			float fRec10 = ((iTemp12) ? fTemp13 : fSlow12 + fRec9[1] + fSlow13 * fTemp11);
			fRec5[0] = (2.0f * fRec10 + -1.0f) * (1.0f - 0.5f * fTemp10) + 0.5f * fTemp10 * (2.0f * fRec7 + -1.0f) - (fRec5[2] * ((fTemp4 + -1.4142135f) / fTemp3 + 1.0f) + 2.0f * fRec5[1] * (1.0f - 1.0f / PadEvolve_faustpower2_f(fTemp3))) / fTemp5;
			float fTemp14 = fSlow14 * ((fRec5[2] + fRec5[0] + 2.0f * fRec5[1]) * std::max<float>(0.0f, std::min<float>(fSlow6 * fRec4[0], std::max<float>(fConst4 * (fSlow5 - fRec4[0]) + 1.0f, 0.8f)) * (1.0f - fSlow4 * float(iRec3[0]))) / fTemp5);
			output0[i0] = FAUSTFLOAT(fTemp14);
			output1[i0] = FAUSTFLOAT(fTemp14);
			iVec1[1] = iVec1[0];
			fRec1[1] = fRec1[0];
			fRec2[1] = fRec2[0];
			fVec2[1] = fVec2[0];
			iRec3[1] = iRec3[0];
			fRec4[1] = fRec4[0];
			fRec6[1] = fRec6[0];
			fRec8[1] = fRec8[0];
			fRec9[1] = fRec9[0];
			fRec5[2] = fRec5[1];
			fRec5[1] = fRec5[0];
		}
	}

};

#endif

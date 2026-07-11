/* ------------------------------------------------------------
name: "timpani"
Code generated with Faust 2.70.3 (https://faust.grame.fr)
Compilation options: -lang cpp -ct 1 -cn Timpani -es 1 -mcd 16 -mdd 1024 -mdy 33 -single -ftz 0
------------------------------------------------------------ */

#ifndef  __Timpani_H__
#define  __Timpani_H__

#ifndef FAUSTFLOAT
#define FAUSTFLOAT float
#endif 

#include <algorithm>
#include <cmath>
#include <cstdint>
#include <math.h>

#ifndef FAUSTCLASS 
#define FAUSTCLASS Timpani
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

class TimpaniSIG0 {
	
  private:
	
	int iVec2[2];
	int iRec6[2];
	
  public:
	
	int getNumInputsTimpaniSIG0() {
		return 0;
	}
	int getNumOutputsTimpaniSIG0() {
		return 1;
	}
	
	void instanceInitTimpaniSIG0(int sample_rate) {
		for (int l7 = 0; l7 < 2; l7 = l7 + 1) {
			iVec2[l7] = 0;
		}
		for (int l8 = 0; l8 < 2; l8 = l8 + 1) {
			iRec6[l8] = 0;
		}
	}
	
	void fillTimpaniSIG0(int count, float* table) {
		for (int i1 = 0; i1 < count; i1 = i1 + 1) {
			iVec2[0] = 1;
			iRec6[0] = (iVec2[1] + iRec6[1]) % 65536;
			table[i1] = std::sin(9.58738e-05f * float(iRec6[0]));
			iVec2[1] = iVec2[0];
			iRec6[1] = iRec6[0];
		}
	}

};

static TimpaniSIG0* newTimpaniSIG0() { return (TimpaniSIG0*)new TimpaniSIG0(); }
static void deleteTimpaniSIG0(TimpaniSIG0* dsp) { delete dsp; }

static float Timpani_faustpower2_f(float value) {
	return value * value;
}
static float ftbl0TimpaniSIG0[65536];

class Timpani : public dsp {
	
 private:
	
	int iVec0[2];
	int fSampleRate;
	float fConst0;
	float fConst2;
	float fConst4;
	float fConst6;
	FAUSTFLOAT fHslider0;
	float fConst7;
	FAUSTFLOAT fButton0;
	float fVec1[2];
	int iRec2[2];
	float fConst8;
	float fConst9;
	float fConst10;
	int iRec3[2];
	float fRec1[3];
	FAUSTFLOAT fHslider1;
	int iRec4[2];
	float fConst11;
	float fRec5[2];
	float fConst12;
	float fConst13;
	FAUSTFLOAT fHslider2;
	float fConst14;
	FAUSTFLOAT fHslider3;
	float fConst15;
	float fRec7[2];
	FAUSTFLOAT fHslider4;
	float fRec0[3];
	float fConst16;
	
 public:
	Timpani() {}

	void metadata(Meta* m) { 
		m->declare("basics.lib/name", "Faust Basic Element Library");
		m->declare("basics.lib/tabulateNd", "Copyright (C) 2023 Bart Brouns <bart@magnetophon.nl>");
		m->declare("basics.lib/version", "1.12.0");
		m->declare("compile_options", "-lang cpp -ct 1 -cn Timpani -es 1 -mcd 16 -mdd 1024 -mdy 33 -single -ftz 0");
		m->declare("envelopes.lib/adsr:author", "Yann Orlarey and Andrey Bundin");
		m->declare("envelopes.lib/ar:author", "Yann Orlarey, Stéphane Letz");
		m->declare("envelopes.lib/author", "GRAME");
		m->declare("envelopes.lib/copyright", "GRAME");
		m->declare("envelopes.lib/license", "LGPL with exception");
		m->declare("envelopes.lib/name", "Faust Envelope Library");
		m->declare("envelopes.lib/version", "1.3.0");
		m->declare("filename", "timpani.dsp");
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
		m->declare("filters.lib/resonlp:author", "Julius O. Smith III");
		m->declare("filters.lib/resonlp:copyright", "Copyright (C) 2003-2019 by Julius O. Smith III <jos@ccrma.stanford.edu>");
		m->declare("filters.lib/resonlp:license", "MIT-style STK-4.3 license");
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
		m->declare("name", "timpani");
		m->declare("noises.lib/name", "Faust Noise Generator Library");
		m->declare("noises.lib/version", "1.4.0");
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
		TimpaniSIG0* sig0 = newTimpaniSIG0();
		sig0->instanceInitTimpaniSIG0(sample_rate);
		sig0->fillTimpaniSIG0(65536, ftbl0TimpaniSIG0);
		deleteTimpaniSIG0(sig0);
	}
	
	virtual void instanceConstants(int sample_rate) {
		fSampleRate = sample_rate;
		fConst0 = std::min<float>(1.92e+05f, std::max<float>(1.0f, float(fSampleRate)));
		float fConst1 = std::tan(5340.7075f / fConst0);
		fConst2 = 2.0f * (1.0f - 1.0f / Timpani_faustpower2_f(fConst1));
		float fConst3 = 1.0f / fConst1;
		fConst4 = (fConst3 + -1.4142135f) / fConst1 + 1.0f;
		float fConst5 = (fConst3 + 1.4142135f) / fConst1 + 1.0f;
		fConst6 = 1.0f / fConst5;
		fConst7 = 10.995574f / fConst0;
		fConst8 = std::max<float>(1.0f, 0.001f * fConst0);
		fConst9 = 1.0f / fConst8;
		fConst10 = 1.0f / std::max<float>(1.0f, 0.018f * fConst0);
		fConst11 = 1.0f / std::max<float>(1.0f, 0.25f * fConst0);
		fConst12 = std::max<float>(1.0f, 0.002f * fConst0);
		fConst13 = 1.0f / fConst12;
		fConst14 = 1.0f / std::max<float>(1.0f, 0.09f * fConst0);
		fConst15 = 1.0f / fConst0;
		fConst16 = 0.835f / fConst5;
	}
	
	virtual void instanceResetUserInterface() {
		fHslider0 = FAUSTFLOAT(82.0f);
		fButton0 = FAUSTFLOAT(0.0f);
		fHslider1 = FAUSTFLOAT(0.5f);
		fHslider2 = FAUSTFLOAT(1.1f);
		fHslider3 = FAUSTFLOAT(0.06f);
		fHslider4 = FAUSTFLOAT(0.7f);
	}
	
	virtual void instanceClear() {
		for (int l0 = 0; l0 < 2; l0 = l0 + 1) {
			iVec0[l0] = 0;
		}
		for (int l1 = 0; l1 < 2; l1 = l1 + 1) {
			fVec1[l1] = 0.0f;
		}
		for (int l2 = 0; l2 < 2; l2 = l2 + 1) {
			iRec2[l2] = 0;
		}
		for (int l3 = 0; l3 < 2; l3 = l3 + 1) {
			iRec3[l3] = 0;
		}
		for (int l4 = 0; l4 < 3; l4 = l4 + 1) {
			fRec1[l4] = 0.0f;
		}
		for (int l5 = 0; l5 < 2; l5 = l5 + 1) {
			iRec4[l5] = 0;
		}
		for (int l6 = 0; l6 < 2; l6 = l6 + 1) {
			fRec5[l6] = 0.0f;
		}
		for (int l9 = 0; l9 < 2; l9 = l9 + 1) {
			fRec7[l9] = 0.0f;
		}
		for (int l10 = 0; l10 < 3; l10 = l10 + 1) {
			fRec0[l10] = 0.0f;
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
	
	virtual Timpani* clone() {
		return new Timpani();
	}
	
	virtual int getSampleRate() {
		return fSampleRate;
	}
	
	virtual void buildUserInterface(UI* ui_interface) {
		ui_interface->openVerticalBox("timpani");
		ui_interface->addHorizontalSlider("bend", &fHslider3, FAUSTFLOAT(0.06f), FAUSTFLOAT(0.0f), FAUSTFLOAT(0.2f), FAUSTFLOAT(0.001f));
		ui_interface->addHorizontalSlider("decay", &fHslider2, FAUSTFLOAT(1.1f), FAUSTFLOAT(0.3f), FAUSTFLOAT(3.0f), FAUSTFLOAT(0.01f));
		ui_interface->addHorizontalSlider("freq", &fHslider0, FAUSTFLOAT(82.0f), FAUSTFLOAT(2e+01f), FAUSTFLOAT(2e+03f), FAUSTFLOAT(0.001f));
		ui_interface->addHorizontalSlider("gain", &fHslider4, FAUSTFLOAT(0.7f), FAUSTFLOAT(0.0f), FAUSTFLOAT(1.0f), FAUSTFLOAT(0.01f));
		ui_interface->addButton("gate", &fButton0);
		ui_interface->addHorizontalSlider("mallet", &fHslider1, FAUSTFLOAT(0.5f), FAUSTFLOAT(0.0f), FAUSTFLOAT(1.2f), FAUSTFLOAT(0.01f));
		ui_interface->closeBox();
	}
	
	virtual void compute(int count, FAUSTFLOAT** RESTRICT inputs, FAUSTFLOAT** RESTRICT outputs) {
		FAUSTFLOAT* output0 = outputs[0];
		FAUSTFLOAT* output1 = outputs[1];
		float fSlow0 = float(fHslider0);
		float fSlow1 = std::tan(fConst7 * fSlow0);
		float fSlow2 = 2.0f * (1.0f - 1.0f / Timpani_faustpower2_f(fSlow1));
		float fSlow3 = 1.0f / fSlow1;
		float fSlow4 = (fSlow3 + -0.4f) / fSlow1 + 1.0f;
		float fSlow5 = (fSlow3 + 0.4f) / fSlow1 + 1.0f;
		float fSlow6 = 1.0f / fSlow5;
		float fSlow7 = float(fButton0);
		float fSlow8 = float(fHslider1) / fSlow5;
		int iSlow9 = fSlow7 == 0.0f;
		float fSlow10 = 1.0f / std::max<float>(1.0f, fConst0 * float(fHslider2));
		float fSlow11 = float(fHslider3);
		float fSlow12 = fConst15 * fSlow0;
		float fSlow13 = float(fHslider4);
		for (int i0 = 0; i0 < count; i0 = i0 + 1) {
			iVec0[0] = 1;
			fVec1[0] = fSlow7;
			iRec2[0] = (fSlow7 > fVec1[1]) + (fSlow7 <= fVec1[1]) * (iRec2[1] + (iRec2[1] > 0));
			float fTemp0 = float(iRec2[0]);
			float fTemp1 = fConst9 * fTemp0;
			float fTemp2 = fConst8 - fTemp0;
			iRec3[0] = 1103515245 * iRec3[1] + 12345;
			fRec1[0] = 4.656613e-10f * float(iRec3[0]) * std::max<float>(0.0f, std::min<float>(fTemp1, fConst10 * fTemp2 + 1.0f)) - fSlow6 * (fSlow4 * fRec1[2] + fSlow2 * fRec1[1]);
			iRec4[0] = iSlow9 * (iRec4[1] + 1);
			fRec5[0] = fSlow7 + fRec5[1] * float(fVec1[1] >= fSlow7);
			float fTemp3 = ((1 - iVec0[1]) ? 0.0f : fRec7[1] + fSlow12 * (fSlow11 * std::max<float>(0.0f, std::min<float>(fTemp1, fConst14 * fTemp2 + 1.0f)) + 1.0f));
			fRec7[0] = fTemp3 - std::floor(fTemp3);
			fRec0[0] = fSlow13 * (ftbl0TimpaniSIG0[std::max<int>(0, std::min<int>(int(65536.0f * fRec7[0]), 65535))] * std::max<float>(0.0f, std::min<float>(fConst13 * fRec5[0], std::max<float>(fSlow10 * (fConst12 - fRec5[0]) + 1.0f, 0.0f)) * (1.0f - fConst11 * float(iRec4[0]))) + fSlow8 * (fRec1[2] + fRec1[0] + 2.0f * fRec1[1])) - fConst6 * (fConst4 * fRec0[2] + fConst2 * fRec0[1]);
			float fTemp4 = fConst16 * (fRec0[2] + fRec0[0] + 2.0f * fRec0[1]);
			output0[i0] = FAUSTFLOAT(fTemp4);
			output1[i0] = FAUSTFLOAT(fTemp4);
			iVec0[1] = iVec0[0];
			fVec1[1] = fVec1[0];
			iRec2[1] = iRec2[0];
			iRec3[1] = iRec3[0];
			fRec1[2] = fRec1[1];
			fRec1[1] = fRec1[0];
			iRec4[1] = iRec4[0];
			fRec5[1] = fRec5[0];
			fRec7[1] = fRec7[0];
			fRec0[2] = fRec0[1];
			fRec0[1] = fRec0[0];
		}
	}

};

#endif

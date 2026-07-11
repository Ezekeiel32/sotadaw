/* ------------------------------------------------------------
name: "bandoneon"
Code generated with Faust 2.70.3 (https://faust.grame.fr)
Compilation options: -lang cpp -ct 1 -cn Bandoneon -es 1 -mcd 16 -mdd 1024 -mdy 33 -single -ftz 0
------------------------------------------------------------ */

#ifndef  __Bandoneon_H__
#define  __Bandoneon_H__

#ifndef FAUSTFLOAT
#define FAUSTFLOAT float
#endif 

#include <algorithm>
#include <cmath>
#include <cstdint>
#include <math.h>

#ifndef FAUSTCLASS 
#define FAUSTCLASS Bandoneon
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

class BandoneonSIG0 {
	
  private:
	
	int iVec8[2];
	int iRec13[2];
	
  public:
	
	int getNumInputsBandoneonSIG0() {
		return 0;
	}
	int getNumOutputsBandoneonSIG0() {
		return 1;
	}
	
	void instanceInitBandoneonSIG0(int sample_rate) {
		for (int l18 = 0; l18 < 2; l18 = l18 + 1) {
			iVec8[l18] = 0;
		}
		for (int l19 = 0; l19 < 2; l19 = l19 + 1) {
			iRec13[l19] = 0;
		}
	}
	
	void fillBandoneonSIG0(int count, float* table) {
		for (int i1 = 0; i1 < count; i1 = i1 + 1) {
			iVec8[0] = 1;
			iRec13[0] = (iVec8[1] + iRec13[1]) % 65536;
			table[i1] = std::sin(9.58738e-05f * float(iRec13[0]));
			iVec8[1] = iVec8[0];
			iRec13[1] = iRec13[0];
		}
	}

};

static BandoneonSIG0* newBandoneonSIG0() { return (BandoneonSIG0*)new BandoneonSIG0(); }
static void deleteBandoneonSIG0(BandoneonSIG0* dsp) { delete dsp; }

static float Bandoneon_faustpower2_f(float value) {
	return value * value;
}
static float ftbl0BandoneonSIG0[65536];

class Bandoneon : public dsp {
	
 private:
	
	int iVec0[2];
	int fSampleRate;
	float fConst0;
	float fConst3;
	float fConst5;
	float fConst7;
	int iRec1[2];
	FAUSTFLOAT fHslider0;
	float fRec0[3];
	FAUSTFLOAT fButton0;
	float fVec1[2];
	int iRec2[2];
	float fConst8;
	float fConst9;
	float fConst10;
	float fConst11;
	FAUSTFLOAT fHslider1;
	float fConst12;
	FAUSTFLOAT fHslider2;
	FAUSTFLOAT fHslider3;
	float fConst13;
	float fRec4[2];
	float fVec2[2];
	float fConst14;
	int IOTA0;
	float fVec3[2048];
	float fConst15;
	float fRec5[2];
	float fVec4[2];
	float fVec5[2048];
	float fRec6[2];
	float fVec6[2];
	float fVec7[2048];
	float fRec7[2];
	float fRec9[2];
	float fRec11[2];
	float fRec3[3];
	FAUSTFLOAT fHslider4;
	float fRec14[2];
	FAUSTFLOAT fHslider5;
	int iRec15[2];
	FAUSTFLOAT fHslider6;
	float fRec16[2];
	FAUSTFLOAT fHslider7;
	float fConst16;
	FAUSTFLOAT fHslider8;
	
 public:
	Bandoneon() {}

	void metadata(Meta* m) { 
		m->declare("basics.lib/name", "Faust Basic Element Library");
		m->declare("basics.lib/tabulateNd", "Copyright (C) 2023 Bart Brouns <bart@magnetophon.nl>");
		m->declare("basics.lib/version", "1.12.0");
		m->declare("compile_options", "-lang cpp -ct 1 -cn Bandoneon -es 1 -mcd 16 -mdd 1024 -mdy 33 -single -ftz 0");
		m->declare("envelopes.lib/adsr:author", "Yann Orlarey and Andrey Bundin");
		m->declare("envelopes.lib/ar:author", "Yann Orlarey, Stéphane Letz");
		m->declare("envelopes.lib/author", "GRAME");
		m->declare("envelopes.lib/copyright", "GRAME");
		m->declare("envelopes.lib/license", "LGPL with exception");
		m->declare("envelopes.lib/name", "Faust Envelope Library");
		m->declare("envelopes.lib/version", "1.3.0");
		m->declare("filename", "bandoneon.dsp");
		m->declare("filters.lib/fir:author", "Julius O. Smith III");
		m->declare("filters.lib/fir:copyright", "Copyright (C) 2003-2019 by Julius O. Smith III <jos@ccrma.stanford.edu>");
		m->declare("filters.lib/fir:license", "MIT-style STK-4.3 license");
		m->declare("filters.lib/highpass:author", "Julius O. Smith III");
		m->declare("filters.lib/highpass:copyright", "Copyright (C) 2003-2019 by Julius O. Smith III <jos@ccrma.stanford.edu>");
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
		m->declare("name", "bandoneon");
		m->declare("noises.lib/name", "Faust Noise Generator Library");
		m->declare("noises.lib/version", "1.4.0");
		m->declare("oscillators.lib/lf_sawpos:author", "Bart Brouns, revised by Stéphane Letz");
		m->declare("oscillators.lib/lf_sawpos:licence", "STK-4.3");
		m->declare("oscillators.lib/name", "Faust Oscillator Library");
		m->declare("oscillators.lib/saw2ptr:author", "Julius O. Smith III");
		m->declare("oscillators.lib/saw2ptr:license", "STK-4.3");
		m->declare("oscillators.lib/sawN:author", "Julius O. Smith III");
		m->declare("oscillators.lib/sawN:license", "STK-4.3");
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
		BandoneonSIG0* sig0 = newBandoneonSIG0();
		sig0->instanceInitBandoneonSIG0(sample_rate);
		sig0->fillBandoneonSIG0(65536, ftbl0BandoneonSIG0);
		deleteBandoneonSIG0(sig0);
	}
	
	virtual void instanceConstants(int sample_rate) {
		fSampleRate = sample_rate;
		fConst0 = std::min<float>(1.92e+05f, std::max<float>(1.0f, float(fSampleRate)));
		float fConst1 = std::tan(6283.1855f / fConst0);
		float fConst2 = Bandoneon_faustpower2_f(fConst1);
		fConst3 = 2.0f * (1.0f - 1.0f / fConst2);
		float fConst4 = 1.0f / fConst1;
		fConst5 = (fConst4 + -1.4142135f) / fConst1 + 1.0f;
		float fConst6 = (fConst4 + 1.4142135f) / fConst1 + 1.0f;
		fConst7 = 1.0f / fConst6;
		fConst8 = std::max<float>(1.0f, 0.002f * fConst0);
		fConst9 = 1.0f / fConst8;
		fConst10 = 1.0f / std::max<float>(1.0f, 0.05f * fConst0);
		fConst11 = 1.0f / (fConst2 * fConst6);
		fConst12 = 3.1415927f / fConst0;
		fConst13 = 1.0f / fConst0;
		fConst14 = 0.25f * fConst0;
		fConst15 = 0.5f * fConst0;
		fConst16 = 0.1f / std::max<float>(1.0f, 0.12f * fConst0);
	}
	
	virtual void instanceResetUserInterface() {
		fHslider0 = FAUSTFLOAT(0.25f);
		fButton0 = FAUSTFLOAT(0.0f);
		fHslider1 = FAUSTFLOAT(0.6f);
		fHslider2 = FAUSTFLOAT(0.007f);
		fHslider3 = FAUSTFLOAT(262.0f);
		fHslider4 = FAUSTFLOAT(4.5f);
		fHslider5 = FAUSTFLOAT(0.08f);
		fHslider6 = FAUSTFLOAT(0.18f);
		fHslider7 = FAUSTFLOAT(0.03f);
		fHslider8 = FAUSTFLOAT(0.8f);
	}
	
	virtual void instanceClear() {
		for (int l0 = 0; l0 < 2; l0 = l0 + 1) {
			iVec0[l0] = 0;
		}
		for (int l1 = 0; l1 < 2; l1 = l1 + 1) {
			iRec1[l1] = 0;
		}
		for (int l2 = 0; l2 < 3; l2 = l2 + 1) {
			fRec0[l2] = 0.0f;
		}
		for (int l3 = 0; l3 < 2; l3 = l3 + 1) {
			fVec1[l3] = 0.0f;
		}
		for (int l4 = 0; l4 < 2; l4 = l4 + 1) {
			iRec2[l4] = 0;
		}
		for (int l5 = 0; l5 < 2; l5 = l5 + 1) {
			fRec4[l5] = 0.0f;
		}
		for (int l6 = 0; l6 < 2; l6 = l6 + 1) {
			fVec2[l6] = 0.0f;
		}
		IOTA0 = 0;
		for (int l7 = 0; l7 < 2048; l7 = l7 + 1) {
			fVec3[l7] = 0.0f;
		}
		for (int l8 = 0; l8 < 2; l8 = l8 + 1) {
			fRec5[l8] = 0.0f;
		}
		for (int l9 = 0; l9 < 2; l9 = l9 + 1) {
			fVec4[l9] = 0.0f;
		}
		for (int l10 = 0; l10 < 2048; l10 = l10 + 1) {
			fVec5[l10] = 0.0f;
		}
		for (int l11 = 0; l11 < 2; l11 = l11 + 1) {
			fRec6[l11] = 0.0f;
		}
		for (int l12 = 0; l12 < 2; l12 = l12 + 1) {
			fVec6[l12] = 0.0f;
		}
		for (int l13 = 0; l13 < 2048; l13 = l13 + 1) {
			fVec7[l13] = 0.0f;
		}
		for (int l14 = 0; l14 < 2; l14 = l14 + 1) {
			fRec7[l14] = 0.0f;
		}
		for (int l15 = 0; l15 < 2; l15 = l15 + 1) {
			fRec9[l15] = 0.0f;
		}
		for (int l16 = 0; l16 < 2; l16 = l16 + 1) {
			fRec11[l16] = 0.0f;
		}
		for (int l17 = 0; l17 < 3; l17 = l17 + 1) {
			fRec3[l17] = 0.0f;
		}
		for (int l20 = 0; l20 < 2; l20 = l20 + 1) {
			fRec14[l20] = 0.0f;
		}
		for (int l21 = 0; l21 < 2; l21 = l21 + 1) {
			iRec15[l21] = 0;
		}
		for (int l22 = 0; l22 < 2; l22 = l22 + 1) {
			fRec16[l22] = 0.0f;
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
	
	virtual Bandoneon* clone() {
		return new Bandoneon();
	}
	
	virtual int getSampleRate() {
		return fSampleRate;
	}
	
	virtual void buildUserInterface(UI* ui_interface) {
		ui_interface->openVerticalBox("bandoneon");
		ui_interface->addHorizontalSlider("attack", &fHslider7, FAUSTFLOAT(0.03f), FAUSTFLOAT(0.003f), FAUSTFLOAT(0.4f), FAUSTFLOAT(0.001f));
		ui_interface->addHorizontalSlider("bellows", &fHslider5, FAUSTFLOAT(0.08f), FAUSTFLOAT(0.0f), FAUSTFLOAT(0.3f), FAUSTFLOAT(0.01f));
		ui_interface->addHorizontalSlider("bellowsrate", &fHslider4, FAUSTFLOAT(4.5f), FAUSTFLOAT(0.0f), FAUSTFLOAT(8.0f), FAUSTFLOAT(0.01f));
		ui_interface->addHorizontalSlider("chiff", &fHslider0, FAUSTFLOAT(0.25f), FAUSTFLOAT(0.0f), FAUSTFLOAT(1.0f), FAUSTFLOAT(0.01f));
		ui_interface->addHorizontalSlider("freq", &fHslider3, FAUSTFLOAT(262.0f), FAUSTFLOAT(55.0f), FAUSTFLOAT(2e+03f), FAUSTFLOAT(0.001f));
		ui_interface->addHorizontalSlider("gain", &fHslider8, FAUSTFLOAT(0.8f), FAUSTFLOAT(0.0f), FAUSTFLOAT(1.0f), FAUSTFLOAT(0.01f));
		ui_interface->addButton("gate", &fButton0);
		ui_interface->addHorizontalSlider("musette", &fHslider2, FAUSTFLOAT(0.007f), FAUSTFLOAT(0.0f), FAUSTFLOAT(0.02f), FAUSTFLOAT(0.0001f));
		ui_interface->addHorizontalSlider("reed", &fHslider1, FAUSTFLOAT(0.6f), FAUSTFLOAT(0.0f), FAUSTFLOAT(1.0f), FAUSTFLOAT(0.01f));
		ui_interface->addHorizontalSlider("release", &fHslider6, FAUSTFLOAT(0.18f), FAUSTFLOAT(0.02f), FAUSTFLOAT(1.2f), FAUSTFLOAT(0.001f));
		ui_interface->closeBox();
	}
	
	virtual void compute(int count, FAUSTFLOAT** RESTRICT inputs, FAUSTFLOAT** RESTRICT outputs) {
		FAUSTFLOAT* output0 = outputs[0];
		FAUSTFLOAT* output1 = outputs[1];
		float fSlow0 = 1.3969839e-10f * float(fHslider0);
		float fSlow1 = float(fButton0);
		float fSlow2 = std::tan(fConst12 * (5e+03f * float(fHslider1) + 1.5e+03f));
		float fSlow3 = 2.0f * (1.0f - 1.0f / Bandoneon_faustpower2_f(fSlow2));
		float fSlow4 = 1.0f / fSlow2;
		float fSlow5 = (fSlow4 + -1.4142135f) / fSlow2 + 1.0f;
		float fSlow6 = 1.0f / ((fSlow4 + 1.4142135f) / fSlow2 + 1.0f);
		float fSlow7 = float(fHslider2);
		float fSlow8 = float(fHslider3);
		float fSlow9 = fSlow8 * (fSlow7 + 1.0f);
		float fSlow10 = std::max<float>(fSlow9, 23.44895f);
		float fSlow11 = std::max<float>(2e+01f, std::fabs(fSlow10));
		float fSlow12 = fConst13 * fSlow11;
		float fSlow13 = fConst14 / fSlow11;
		float fSlow14 = std::max<float>(0.0f, std::min<float>(2047.0f, fConst15 / fSlow10));
		int iSlow15 = int(fSlow14);
		int iSlow16 = iSlow15 + 1;
		float fSlow17 = std::floor(fSlow14);
		float fSlow18 = fSlow14 - fSlow17;
		float fSlow19 = fSlow17 + (1.0f - fSlow14);
		float fSlow20 = std::max<float>(fSlow8, 23.44895f);
		float fSlow21 = std::max<float>(2e+01f, std::fabs(fSlow20));
		float fSlow22 = fConst13 * fSlow21;
		float fSlow23 = fConst14 / fSlow21;
		float fSlow24 = std::max<float>(0.0f, std::min<float>(2047.0f, fConst15 / fSlow20));
		int iSlow25 = int(fSlow24);
		int iSlow26 = iSlow25 + 1;
		float fSlow27 = std::floor(fSlow24);
		float fSlow28 = fSlow24 - fSlow27;
		float fSlow29 = fSlow27 + (1.0f - fSlow24);
		float fSlow30 = fSlow8 * (1.0f - fSlow7);
		float fSlow31 = std::max<float>(fSlow30, 23.44895f);
		float fSlow32 = std::max<float>(2e+01f, std::fabs(fSlow31));
		float fSlow33 = fConst13 * fSlow32;
		float fSlow34 = fConst14 / fSlow32;
		float fSlow35 = std::max<float>(0.0f, std::min<float>(2047.0f, fConst15 / fSlow31));
		int iSlow36 = int(fSlow35);
		int iSlow37 = iSlow36 + 1;
		float fSlow38 = std::floor(fSlow35);
		float fSlow39 = fSlow35 - fSlow38;
		float fSlow40 = fSlow38 + (1.0f - fSlow35);
		float fSlow41 = std::max<float>(1.1920929e-07f, std::fabs(fSlow9));
		float fSlow42 = fConst13 * fSlow41;
		float fSlow43 = 1.0f - fConst0 / fSlow41;
		float fSlow44 = std::max<float>(1.1920929e-07f, std::fabs(fSlow8));
		float fSlow45 = fConst13 * fSlow44;
		float fSlow46 = 1.0f - fConst0 / fSlow44;
		float fSlow47 = std::max<float>(1.1920929e-07f, std::fabs(fSlow30));
		float fSlow48 = fConst13 * fSlow47;
		float fSlow49 = 1.0f - fConst0 / fSlow47;
		float fSlow50 = fConst13 * float(fHslider4);
		float fSlow51 = float(fHslider5);
		int iSlow52 = fSlow1 == 0.0f;
		float fSlow53 = 1.0f / std::max<float>(1.0f, fConst0 * float(fHslider6));
		float fSlow54 = std::max<float>(1.0f, fConst0 * float(fHslider7));
		float fSlow55 = 1.0f / fSlow54;
		float fSlow56 = 0.45f * float(fHslider8);
		for (int i0 = 0; i0 < count; i0 = i0 + 1) {
			iVec0[0] = 1;
			iRec1[0] = 1103515245 * iRec1[1] + 12345;
			fRec0[0] = fSlow0 * float(iRec1[0]) - fConst7 * (fConst5 * fRec0[2] + fConst3 * fRec0[1]);
			fVec1[0] = fSlow1;
			iRec2[0] = (iRec2[1] + (iRec2[1] > 0)) * (fSlow1 <= fVec1[1]) + (fSlow1 > fVec1[1]);
			float fTemp0 = float(iRec2[0]);
			int iTemp1 = 1 - iVec0[1];
			float fTemp2 = ((iTemp1) ? 0.0f : fSlow12 + fRec4[1]);
			fRec4[0] = fTemp2 - std::floor(fTemp2);
			float fTemp3 = Bandoneon_faustpower2_f(2.0f * fRec4[0] + -1.0f);
			fVec2[0] = fTemp3;
			float fTemp4 = float(iVec0[1]);
			float fTemp5 = fSlow13 * fTemp4 * (fTemp3 - fVec2[1]);
			fVec3[IOTA0 & 2047] = fTemp5;
			float fTemp6 = ((iTemp1) ? 0.0f : fSlow22 + fRec5[1]);
			fRec5[0] = fTemp6 - std::floor(fTemp6);
			float fTemp7 = Bandoneon_faustpower2_f(2.0f * fRec5[0] + -1.0f);
			fVec4[0] = fTemp7;
			float fTemp8 = fSlow23 * fTemp4 * (fTemp7 - fVec4[1]);
			fVec5[IOTA0 & 2047] = fTemp8;
			float fTemp9 = ((iTemp1) ? 0.0f : fSlow33 + fRec6[1]);
			fRec6[0] = fTemp9 - std::floor(fTemp9);
			float fTemp10 = Bandoneon_faustpower2_f(2.0f * fRec6[0] + -1.0f);
			fVec6[0] = fTemp10;
			float fTemp11 = fSlow34 * fTemp4 * (fTemp10 - fVec6[1]);
			fVec7[IOTA0 & 2047] = fTemp11;
			float fTemp12 = fSlow42 + fRec7[1] + -1.0f;
			int iTemp13 = fTemp12 < 0.0f;
			float fTemp14 = fSlow42 + fRec7[1];
			fRec7[0] = ((iTemp13) ? fTemp14 : fTemp12);
			float fRec8 = ((iTemp13) ? fTemp14 : fSlow42 + fRec7[1] + fSlow43 * fTemp12);
			float fTemp15 = fSlow45 + fRec9[1] + -1.0f;
			int iTemp16 = fTemp15 < 0.0f;
			float fTemp17 = fSlow45 + fRec9[1];
			fRec9[0] = ((iTemp16) ? fTemp17 : fTemp15);
			float fRec10 = ((iTemp16) ? fTemp17 : fSlow45 + fRec9[1] + fSlow46 * fTemp15);
			float fTemp18 = fSlow48 + fRec11[1] + -1.0f;
			int iTemp19 = fTemp18 < 0.0f;
			float fTemp20 = fSlow48 + fRec11[1];
			fRec11[0] = ((iTemp19) ? fTemp20 : fTemp18);
			float fRec12 = ((iTemp19) ? fTemp20 : fSlow48 + fRec11[1] + fSlow49 * fTemp18);
			fRec3[0] = 0.33333334f * (0.6f * (2.0f * fRec12 + -1.0f + 2.0f * fRec10 + -1.0f + 2.0f * fRec8 + -1.0f) + 0.4f * (fTemp11 - (fSlow40 * fVec7[(IOTA0 - iSlow36) & 2047] + fSlow39 * fVec7[(IOTA0 - iSlow37) & 2047]) + (fTemp8 - (fSlow29 * fVec5[(IOTA0 - iSlow25) & 2047] + fSlow28 * fVec5[(IOTA0 - iSlow26) & 2047])) + (fTemp5 - (fSlow19 * fVec3[(IOTA0 - iSlow15) & 2047] + fSlow18 * fVec3[(IOTA0 - iSlow16) & 2047])))) - fSlow6 * (fSlow5 * fRec3[2] + fSlow3 * fRec3[1]);
			float fTemp21 = ((iTemp1) ? 0.0f : fSlow50 + fRec14[1]);
			fRec14[0] = fTemp21 - std::floor(fTemp21);
			iRec15[0] = iSlow52 * (iRec15[1] + 1);
			fRec16[0] = fSlow1 + fRec16[1] * float(fVec1[1] >= fSlow1);
			float fTemp22 = fSlow56 * std::max<float>(0.0f, std::min<float>(fSlow55 * fRec16[0], std::max<float>(fConst16 * (fSlow54 - fRec16[0]) + 1.0f, 0.9f)) * (1.0f - fSlow53 * float(iRec15[0]))) * (fSlow51 * ftbl0BandoneonSIG0[std::max<int>(0, std::min<int>(int(65536.0f * fRec14[0]), 65535))] + 1.0f) * (fSlow6 * (fRec3[2] + fRec3[0] + 2.0f * fRec3[1]) + fConst11 * std::max<float>(0.0f, std::min<float>(fConst9 * fTemp0, fConst10 * (fConst8 - fTemp0) + 1.0f)) * (fRec0[0] + fRec0[2] - 2.0f * fRec0[1]));
			output0[i0] = FAUSTFLOAT(fTemp22);
			output1[i0] = FAUSTFLOAT(fTemp22);
			iVec0[1] = iVec0[0];
			iRec1[1] = iRec1[0];
			fRec0[2] = fRec0[1];
			fRec0[1] = fRec0[0];
			fVec1[1] = fVec1[0];
			iRec2[1] = iRec2[0];
			fRec4[1] = fRec4[0];
			fVec2[1] = fVec2[0];
			IOTA0 = IOTA0 + 1;
			fRec5[1] = fRec5[0];
			fVec4[1] = fVec4[0];
			fRec6[1] = fRec6[0];
			fVec6[1] = fVec6[0];
			fRec7[1] = fRec7[0];
			fRec9[1] = fRec9[0];
			fRec11[1] = fRec11[0];
			fRec3[2] = fRec3[1];
			fRec3[1] = fRec3[0];
			fRec14[1] = fRec14[0];
			iRec15[1] = iRec15[0];
			fRec16[1] = fRec16[0];
		}
	}

};

#endif
